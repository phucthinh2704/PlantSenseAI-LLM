"""
classify.py — CNN phân loại loại cây và bệnh từ ảnh.

Tương thích: TensorFlow 2.16+ / Keras 3
Không dùng tf.keras.preprocessing (deprecated trong Keras 3).
Xử lý ảnh hoàn toàn bằng PIL + NumPy.
"""
from __future__ import annotations

import contextlib
import io
import json
import logging
import os
import sys

# ── Tắt log TF/Keras TRƯỚC khi import tensorflow ──────────────────────────────
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import numpy as np
import tensorflow as tf

tf.get_logger().setLevel("ERROR")
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("keras").setLevel(logging.ERROR)

try:
    import absl.logging as _absl_log
    _absl_log.set_verbosity(_absl_log.ERROR)
except Exception:
    pass

# Keras 3: import keras trực tiếp (không qua tf.keras) để load .keras format
try:
    import keras
    _keras_load_model = keras.models.load_model
except ImportError:
    # fallback cho TF cũ
    _keras_load_model = tf.keras.models.load_model

import timm
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

logger = logging.getLogger(__name__)

# ── Đường dẫn (BASE_DIR = thư mục "app/") ─────────────────────────────────────
_HERE     = os.path.dirname(os.path.abspath(__file__))
BASE_DIR  = os.path.dirname(_HERE)   # app/

PLANT_LABEL_PATH  = os.path.join(BASE_DIR, "cnn", "label", "label.json")
PLANT_MODEL_PATH  = os.path.join(BASE_DIR, "cnn", "model", "convnextv2_mango_rice.pth")

RICE_MODEL_PATH   = os.path.join(BASE_DIR, "cnn", "model", "resnet101_rice_disease.keras")
RICE_LABELS_JSON  = os.path.join(BASE_DIR, "cnn", "label", "label_rice_disease.json")

# Đổi sang model xoài riêng nếu có; hiện dùng fallback rice model
MANGO_MODEL_PATH  = os.path.join(BASE_DIR, "cnn", "model", "resnet101_rice_disease.keras")
MANGO_LABELS_JSON = os.path.join(BASE_DIR, "cnn", "label", "label_mango_disease.json")

DISEASE_NAME_JSON = os.path.join(BASE_DIR, "cnn", "label", "label_name_disease.json")

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Singleton cache ────────────────────────────────────────────────────────────
_plant_model:      nn.Module | None = None
_plant_classes:    list | None      = None
_rice_model:       object | None    = None
_rice_classes:     list | None      = None
_mango_model:      object | None    = None
_mango_classes:    list | None      = None
_disease_name_map: dict | None      = None


# ── Helpers ────────────────────────────────────────────────────────────────────
def _load_index_labels(path: str) -> list[str]:
    """Đọc label JSON dạng {"0": "name", "1": "name", ...} → list theo thứ tự index."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [raw[str(i)] for i in range(len(raw))]


def _build_convnext(num_classes: int) -> nn.Module:
    model = timm.create_model(
        "convnextv2_tiny.fcmae_ft_in1k",
        pretrained=False,
        num_classes=0,
    )
    in_features = model.head.in_features
    model.head = nn.Sequential(
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(1),
        nn.Linear(in_features, num_classes),
    )
    return model


def _load_torch_checkpoint(path: str, num_classes: int) -> nn.Module:
    model = _build_convnext(num_classes)
    ckpt = torch.load(path, map_location=_device, weights_only=False)
    state = ckpt.get("model_state_dict", ckpt)
    model.load_state_dict(state, strict=False)
    model.eval().to(_device)
    return model


# Transform ảnh cho PyTorch (ImageNet mean/std)
_torch_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


@contextlib.contextmanager
def _quiet():
    """Tạm thời tắt stdout của Python để giảm log thừa khi load Keras model."""
    with open(os.devnull, "w") as devnull:
        old = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old


# ── Load models (gọi 1 lần khi server start) ──────────────────────────────────
def load_all_models() -> None:
    """
    Load toàn bộ CNN models vào bộ nhớ.
    Phải gọi trong lifespan() trước khi nhận request.
    Mỗi model được load độc lập — lỗi 1 model không chặn model khác.
    """
    global _plant_model, _plant_classes
    global _rice_model,  _rice_classes
    global _mango_model, _mango_classes
    global _disease_name_map

    tf.get_logger().setLevel("ERROR")

    # 1. Plant-type model (ConvNeXtV2, PyTorch)
    try:
        if not os.path.exists(PLANT_MODEL_PATH):
            raise FileNotFoundError(f"File không tồn tại: {PLANT_MODEL_PATH}")
        print(f"[CNN] Loading plant model …")
        _plant_classes = _load_index_labels(PLANT_LABEL_PATH)
        _plant_model   = _load_torch_checkpoint(PLANT_MODEL_PATH, len(_plant_classes))
        print(f"[CNN] ✅ Plant model ready — classes: {_plant_classes}")
    except Exception as exc:
        print(f"[CNN] ❌ Plant model load FAILED: {exc}")
        logger.exception("[CNN] Plant model load failed")

    # 2. Rice disease model (ResNet101, Keras)
    try:
        if not os.path.exists(RICE_MODEL_PATH):
            raise FileNotFoundError(f"File không tồn tại: {RICE_MODEL_PATH}")
        print(f"[CNN] Loading rice disease model …")
        _rice_classes = _load_index_labels(RICE_LABELS_JSON)
        # Keras 3: dùng keras.models.load_model (không phải tf.keras) cho .keras format
        _rice_model = _keras_load_model(RICE_MODEL_PATH, compile=False)
        print(f"[CNN] ✅ Rice model ready — {len(_rice_classes)} classes")
    except Exception as exc:
        print(f"[CNN] ❌ Rice model load FAILED: {exc}")
        logger.exception("[CNN] Rice model load failed")

    # 3. Mango disease model
    try:
        if not os.path.exists(MANGO_MODEL_PATH):
            raise FileNotFoundError(f"File không tồn tại: {MANGO_MODEL_PATH}")
        if MANGO_MODEL_PATH == RICE_MODEL_PATH:
            # Dùng chung object, chỉ đổi labels
            if _rice_model is None:
                raise RuntimeError("Rice model chưa load xong, không thể dùng làm mango fallback")
            _mango_model   = _rice_model
            _mango_classes = _load_index_labels(MANGO_LABELS_JSON)
            print(f"[CNN] Mango model: reusing rice model — {len(_mango_classes)} classes")
        else:
            print(f"[CNN] Loading mango disease model …")
            _mango_classes = _load_index_labels(MANGO_LABELS_JSON)
            _mango_model   = _keras_load_model(MANGO_MODEL_PATH, compile=False)
            print(f"[CNN] ✅ Mango model ready — {len(_mango_classes)} classes")
    except Exception as exc:
        print(f"[CNN] ❌ Mango model load FAILED: {exc}")
        logger.exception("[CNN] Mango model load failed")

    # 4. Disease name map (tên tiếng Việt)
    with open(DISEASE_NAME_JSON, "r", encoding="utf-8") as f:
        _disease_name_map = json.load(f)

    # Tổng kết
    loaded = [
        ("Plant",  _plant_model  is not None),
        ("Rice",   _rice_model   is not None),
        ("Mango",  _mango_model  is not None),
    ]
    for name, ok in loaded:
        status = "✅" if ok else "❌ MISSING"
        print(f"[CNN]   {status}  {name} model")
    print("[CNN] load_all_models() done.")


# ── Inference ──────────────────────────────────────────────────────────────────
def _infer_plant(pil_image: Image.Image) -> tuple[str, float]:
    """Phân loại loại cây bằng ConvNeXtV2 (sử dụng cached model)."""
    tensor = _torch_transform(pil_image.convert("RGB")).unsqueeze(0).to(_device)
    with torch.no_grad():
        logits = _plant_model(tensor)
        probs  = torch.nn.functional.softmax(logits, dim=1)
        idx    = torch.argmax(probs, dim=1).item()
    return _plant_classes[idx], float(probs[0][idx])


def _infer_disease(keras_model, class_names: list, pil_image: Image.Image) -> tuple[str, float]:
    """
    Phân loại bệnh với Keras ResNet101.
    Tiền xử lý thuần PIL + NumPy — không dùng tf.keras.preprocessing (Keras 3 deprecated).
    """
    # Resize + normalize về [0, 1]
    img    = pil_image.convert("RGB").resize((224, 224), Image.BILINEAR)
    arr    = np.array(img, dtype=np.float32) / 255.0        # shape (224, 224, 3)
    batch  = np.expand_dims(arr, axis=0)                    # shape (1, 224, 224, 3)

    preds      = keras_model.predict(batch, verbose=0)       # verbose=0: no progress bar
    class_idx = int(np.argmax(preds, axis=1)[0])
    confidence = float(np.max(preds))
    return class_names[class_idx], confidence


# ── Public API ─────────────────────────────────────────────────────────────────
def classify_image_from_bytes(image_bytes: bytes) -> dict:
    """
    Nhận raw bytes ảnh → phân loại loại cây + bệnh.

    Returns:
        {
          "plant_type":      "rice" | "mango",
          "disease_key":     "leaf_blast",        # key nội bộ
          "disease_name_vi": "Bệnh đạo ôn lá",   # tên tiếng Việt
          "confidence":      0.94,
        }

    Raises:
        RuntimeError: nếu models chưa được load.
    """
    if _plant_model is None:
        raise RuntimeError(
            "CNN models chưa được load. Đảm bảo load_all_models() đã được gọi trong lifespan."
        )

    pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Bước 1 — loại cây
    plant_type, plant_conf = _infer_plant(pil)
    logger.info(f"[CNN] Plant: {plant_type} ({plant_conf:.2%})")

    # Bước 2 — bệnh
    if plant_type == "rice":
        if _rice_model is None:
            raise RuntimeError("Rice disease model chưa load.")
        disease_key, confidence = _infer_disease(_rice_model, _rice_classes, pil)
    elif plant_type == "mango":
        if _mango_model is None:
            raise RuntimeError("Mango disease model chưa load.")
        disease_key, confidence = _infer_disease(_mango_model, _mango_classes, pil)
    else:
        raise ValueError(f"Loại cây không được hỗ trợ: {plant_type}")

    logger.info(f"[CNN] Disease: {disease_key} ({confidence:.2%})")

    # Bước 3 — tên tiếng Việt
    disease_name_vi = _disease_name_map.get(disease_key, disease_key)

    return {
        "plant_type":      plant_type,
        "disease_key":     disease_key,
        "disease_name_vi": disease_name_vi,
        "confidence":      confidence,
    }


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_all_models()
    path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    with open(path, "rb") as f:
        res = classify_image_from_bytes(f.read())
    print(res)
