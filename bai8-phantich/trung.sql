SELECT ma_sv, UPPER(ma_phien) AS ma_phien, COUNT(*) AS so_luong
FROM diem_danh
GROUP BY ma_sv, UPPER(ma_phien)
HAVING COUNT(*) > 1;
