-- Ty le sai: COUNT(scans)/registrations (khong loai trung, khong loai nguoi la)
SELECT
  COUNT(*) AS scans,
  (SELECT COUNT(*) FROM dang_ky) AS registered,
  CASE WHEN (SELECT COUNT(*) FROM dang_ky) = 0 THEN NULL
       ELSE ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dang_ky), 4)
  END AS percent
FROM diem_danh;
