import sys
import asyncio
import logging
from fastapi import HTTPException


async def run_indexing_script(full_reindex: bool = False):
    """
    Thực thi script indexing.py bất đồng bộ.
    """
    command = [
        sys.executable,
        "indexing.py",
    ]  # sys.executable là đường dẫn tới python.exe
    if full_reindex:
        command.append("--full-reindex")

    logging.info(f"Đang thực thi lệnh: {' '.join(command)}")

    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logging.info(f"Indexing thành công: {stdout.decode()}")
            return {"message": "Indexing hoàn tất!", "output": stdout.decode()}
        else:
            logging.error(f"Indexing thất bại: {stderr.decode()}")
            raise HTTPException(
                status_code=500, detail=f"Indexing thất bại: {stderr.decode()}"
            )
    except Exception as e:
        logging.error(f"Lỗi nghiêm trọng khi chạy script indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
