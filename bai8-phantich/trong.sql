SELECT ma_sv, ma_phien, phut_tre
FROM diem_danh
WHERE phut_tre IS NULL OR TRIM(phut_tre) = '';
