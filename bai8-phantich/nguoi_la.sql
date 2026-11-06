SELECT q.ma_sv, q.ma_phien
FROM diem_danh q
LEFT JOIN dang_ky d ON q.ma_sv = d.ma_sv AND UPPER(q.ma_phien) = UPPER(d.ma_phien)
WHERE d.ma_sv IS NULL;
