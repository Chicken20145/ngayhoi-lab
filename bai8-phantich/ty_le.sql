WITH hop_le AS (
  SELECT DISTINCT d.ma_sv, UPPER(d.ma_phien) AS ma_phien
  FROM dang_ky d
  JOIN diem_danh q ON d.ma_sv = q.ma_sv AND UPPER(d.ma_phien) = UPPER(q.ma_phien)
)
SELECT
  COUNT(*) AS attended,
  (SELECT COUNT(*) FROM dang_ky) AS registered,
  CASE WHEN (SELECT COUNT(*) FROM dang_ky) = 0 THEN NULL
       ELSE ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dang_ky), 4)
  END AS percent
FROM hop_le;
