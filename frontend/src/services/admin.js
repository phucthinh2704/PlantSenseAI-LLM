import axios from "@configs/axios";

// API này gọi backend, backend sẽ thực thi: python indexing.py
export const apiRunIncrementalIndex = async () =>
	axios({
		method: "POST",
		url: `/admin/index/run-incremental`,
	});

// API này gọi backend, backend sẽ thực thi: python indexing.py --full-reindex
export const apiRunFullReindex = async () =>
	axios({
		method: "POST",
		url: `/admin/index/run-full-reindex`,
	});