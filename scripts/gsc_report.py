#!/usr/bin/env python3
"""Daily GSC report for skillmdvalidator.com.

Reads the service-account JSON from the GSC_SERVICE_ACCOUNT_JSON env var,
queries Search Analytics (last 28 days, by page and by query) and the URL
Inspection API (index status for every URL in sitemap.xml), and writes a
Markdown report to docs/gsc-report.md plus the Actions job summary.

GSC data lags 2-3 days, so the 28-day window ends 2 days ago.
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

SITE_CANDIDATES = ['https://skillmdvalidator.com/', 'sc-domain:skillmdvalidator.com']
SITEMAP = 'https://skillmdvalidator.com/sitemap.xml'
REPORT = 'docs/gsc-report.md'


def query_search_analytics(svc, site, start, end, dimensions, row_limit):
    body = {
        'startDate': start.isoformat(),
        'endDate': end.isoformat(),
        'dimensions': dimensions,
        'rowLimit': row_limit,
    }
    return svc.searchanalytics().query(siteUrl=site, body=body).execute().get('rows', [])


def main():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    info = json.loads(os.environ['GSC_SERVICE_ACCOUNT_JSON'])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
    svc = build('searchconsole', 'v1', credentials=creds)

    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=27)

    # Try URL-prefix property first, then domain property; use whichever works.
    site = None
    pages = []
    queries = []
    for cand in SITE_CANDIDATES:
        try:
            pages = query_search_analytics(svc, cand, start, end, ['page'], 250)
            queries = query_search_analytics(svc, cand, start, end, ['query'], 25)
            site = cand
            break
        except HttpError as e:
            if e.resp.status in (403, 404):
                print('site %s not accessible (%s), trying next' % (cand, e.resp.status))
                continue
            raise
    if site is None:
        print('ERROR: service account has no access to either property form. '
              'Check that it was added as a user in GSC.', file=sys.stderr)
        sys.exit(1)
    print('using property:', site)

    # Index status for every URL in sitemap.xml.
    data = urllib.request.urlopen(SITEMAP, timeout=30).read()
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [e.text.strip() for e in ET.fromstring(data).findall('s:url/s:loc', ns)]
    inspected = []
    for u in urls:
        try:
            r = svc.urlInspection().index().inspect(
                body={'inspectionUrl': u, 'siteUrl': site}).execute()
            res = r.get('inspectionResult', {}).get('indexStatusResult', {})
            inspected.append((u, res.get('verdict', '?'), res.get('coverageState', '')))
        except HttpError as e:
            inspected.append((u, 'ERROR', 'HTTP %s' % e.resp.status))
        except Exception as e:
            inspected.append((u, 'ERROR', str(e)[:120]))

    lines = []
    lines.append('# GSC 每日报告')
    lines.append('')
    lines.append('统计区间：%s 至 %s（GSC 数据延迟 2~3 天）' % (start, end))
    lines.append('')
    lines.append('## 收录状态（URL Inspection）')
    lines.append('')
    lines.append('| 页面 | 状态 | 覆盖情况 |')
    lines.append('|---|---|---|')
    for u, v, c in inspected:
        lines.append('| %s | %s | %s |' % (u, v, c))
    lines.append('')
    lines.append('## 页面表现（近 28 天）')
    lines.append('')
    if pages:
        lines.append('| 页面 | 点击 | 曝光 | 点击率 | 平均排名 |')
        lines.append('|---|---:|---:|---:|---:|')
        for r in pages:
            lines.append('| %s | %d | %d | %.1f%% | %.1f |' % (
                r['keys'][0], int(r['clicks']), int(r['impressions']),
                r['ctr'] * 100, r['position']))
    else:
        lines.append('暂无数据（新站或 GSC 尚未积累数据）。')
    lines.append('')
    lines.append('## 热门查询词（近 28 天）')
    lines.append('')
    if queries:
        lines.append('| 查询词 | 点击 | 曝光 | 点击率 | 平均排名 |')
        lines.append('|---|---:|---:|---:|---:|')
        for r in queries:
            lines.append('| %s | %d | %d | %.1f%% | %.1f |' % (
                r['keys'][0], int(r['clicks']), int(r['impressions']),
                r['ctr'] * 100, r['position']))
    else:
        lines.append('暂无数据。')
    lines.append('')

    report = '\n'.join(lines)
    os.makedirs('docs', exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'w', encoding='utf-8') as f:
            f.write(report)
    print(report)


if __name__ == '__main__':
    main()
