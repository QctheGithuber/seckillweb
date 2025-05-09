#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高并发秒杀测试脚本（支持指定自身用户 + 随机用户混合，并输出 JSON & Markdown 报告）
"""

import argparse, asyncio, aiohttp, time, statistics, random, json

def parse_args():
    p = argparse.ArgumentParser(description="高并发秒杀测试（含自身账号 & 随机账号）")
    p.add_argument("--host",        type=str, default="http://localhost:8000", help="API 主机")
    p.add_argument("--product",     type=int, required=True,           help="要秒杀的 product_id")
    p.add_argument("--my-user",     type=int, required=True,           help="自身 user_id")
    p.add_argument("--max-user",    type=int, default=10000,           help="随机 user_id 上限")
    p.add_argument("--requests",    type=int, default=1000,            help="总请求数")
    p.add_argument("--concurrency", type=int, default=200,             help="并发量")
    return p.parse_args()

async def send_one(session, sem, url, uid, results):
    async with sem:
        start = time.perf_counter()
        try:
            async with session.post(f"{url}/{uid}") as resp:
                await resp.text()
                latency = time.perf_counter() - start
                results.append({"user": uid, "status": resp.status, "latency": latency})
        except Exception:
            latency = time.perf_counter() - start
            results.append({"user": uid, "status": 0, "latency": latency})

async def main():
    args = parse_args()
    url = f"{args.host}/api/flashsale/{args.product}"
    total = args.requests
    conc  = args.concurrency
    sem   = asyncio.Semaphore(conc)
    results = []

    connector = aiohttp.TCPConnector(limit=conc*2)
    timeout   = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # 准备任务列表：第一个用自身账号，其余用随机账号（排除自身）
        uids = [args.my_user] + [
            (uid := random.randint(1, args.max_user)) if (uid := random.randint(1, args.max_user)) != args.my_user else random.randint(1, args.max_user)
            for _ in range(total - 1)
        ]
        tasks = [asyncio.create_task(send_one(session, sem, f"{args.host}/api/flashsale/{args.product}", uid, results))
                 for uid in uids]
        t0 = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - t0

    # 统计
    statuses = [r["status"] for r in results]
    latencies = [r["latency"] for r in results]
    success = sum(1 for s in statuses if s == 200)
    fail    = total - success
    qps     = total / elapsed
    avg     = statistics.mean(latencies)
    p50     = statistics.median(latencies)
    p90     = statistics.quantiles(latencies, n=10)[8]
    p99     = statistics.quantiles(latencies, n=100)[98]

    report = {
        "product": args.product,
        "my_user": args.my_user,
        "total_requests": total,
        "concurrency": conc,
        "elapsed_s": round(elapsed, 3),
        "qps": round(qps, 2),
        "success_count": success,
        "fail_count": fail,
        "avg_latency_s": round(avg, 4),
        "p50_latency_s": round(p50, 4),
        "p90_latency_s": round(p90, 4),
        "p99_latency_s": round(p99, 4),
    }

    # 写 JSON
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    # 写 Markdown
    with open("report.md", "w") as f:
        f.write("# 秒杀压测报告\n\n")
        for k, v in report.items():
            f.write(f"- **{k.replace('_', ' ').title()}**：{v}\n")
    print("报告已生成：report.json 和 report.md")

if __name__ == "__main__":
    asyncio.run(main())
