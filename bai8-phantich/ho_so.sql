SELECT 'TRUNG' AS danh_muc, ma_sv, UPPER(ma_phien) AS ma_phien, COUNT(*) AS so_luong
FROM diem_danh GROUP BY ma_sv, UPPER(ma_phien) HAVING COUNT(*) > 1;

SELECT 'VIET_THUONG' AS danh_muc, ma_sv, ma_phien
FROM diem_danh WHERE ma_phien != UPPER(ma_phien);

SELECT 'TRONG' AS danh_muc, ma_sv, ma_phien, phut_tre
FROM diem_danh WHERE phut_tre IS NULL OR TRIM(phut_tre) = '';

SELECT 'NGUOI_LA' AS danh_muc, q.ma_sv, q.ma_phien
FROM diem_danh q
LEFT JOIN dang_ky d ON q.ma_sv = d.ma_sv AND UPPER(q.ma_phien) = UPPER(d.ma_phien)
WHERE d.ma_sv IS NULL;
