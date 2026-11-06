SELECT
  UPPER(d.ma_phien) AS session,
  COUNT(*) AS n,
  COUNT(q.ma_sv) AS attended,
  CASE WHEN COUNT(*) = 0 THEN NULL
       ELSE ROUND(COUNT(q.ma_sv) * 100.0 / COUNT(*), 4)
  END AS percent
FROM dang_ky d
LEFT JOIN (
  SELECT DISTINCT ma_sv, UPPER(ma_phien) AS ma_phien
  FROM diem_danh
) q ON d.ma_sv = q.ma_sv AND UPPER(d.ma_phien) = q.ma_phien
GROUP BY UPPER(d.ma_phien)
ORDER BY session;
