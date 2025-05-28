SELECT
  user_email,
  DATE(date) AS data_envio,
  COUNT(*) AS total_pdfs
FROM `neogov-default.arquivos.relatorios_uploads`
WHERE DATE(date) = CURRENT_DATE("America/Sao_Paulo")
GROUP BY user_email, data_envio
ORDER BY data_envio DESC;
