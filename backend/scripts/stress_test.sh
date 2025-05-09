# Bash 版本：`stress_test.sh`
```bash
#!/usr/bin/env bash
# stress_test.sh — 针对指定产品和自身用户，混合随机用户的高并发秒杀测试并生成报告

# 配置区
HOST="http://localhost:8000"
PRODUCT=7        # 要测试的 product_id
MY_USER=33       # 你自己的 user_id（脚本中固定第一条请求）
TOTAL=1000       # 总请求数
CONC=200         # 并发量
MAX_USER=10000   # 随机其他用户 ID 范围 1–MAX_USER

URL="$HOST/api/flashsale"
LOGFILE="report.bash.log"
REPORT_MD="report.md"

# 清理旧文件
rm -f "$LOGFILE" "$REPORT_MD"

# 生成用户列表：第一个是 MY_USER，其余随机（排除 MY_USER）
user_ids=()
for ((i=1; i<=TOTAL; i++)); do
  if [ "$i" -eq 1 ]; then
    user_ids+=("$MY_USER")
  else
    while :; do
      uid=$((RANDOM % MAX_USER + 1))
      [ "$uid" -ne "$MY_USER" ] && break
    done
    user_ids+=("$uid")
  fi
done

# 并发发请求，记录 "状态码 延迟" 到日志
printf "%s\n" "${user_ids[@]}" | \
xargs -n1 -P"$CONC" -I% bash -c '
  start=$(date +%s.%N)
  status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "'"$URL"'/%/'"$PRODUCT"'" )
  end=$(date +%s.%N)
  latency=$(echo "$end - $start" | bc)
  echo "$status $latency"
' >> "$LOGFILE"

# 统计并生成 Markdown 报告
total=$(wc -l < "$LOGFILE")
success=$(awk '$1==200{c++} END{print c+0}' "$LOGFILE")
fail=$((total - success))
avg_latency=$(awk '{sum+=$2} END{if(NR>0) printf "%.3f", sum/NR}' "$LOGFILE")

cat <<EOF > "$REPORT_MD"
# 秒杀压测报告

- **产品 ID**：$PRODUCT  
- **自身用户 ID**：$MY_USER  
- **总请求数**：$total  
- **并发数**：$CONC  
- **成功数 (HTTP 200)**：$success  
- **失败数**：$fail  
- **平均延迟**：${avg_latency}s  

EOF

echo "报告生成完毕：$REPORT_MD"
