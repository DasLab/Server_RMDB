## Maintenance for RMDB ops

#### 0. 500 Errors:
- Investigate **immediately** (you get admin email notice)
- Hot fix or escalate issue, or disable

#### 1. AWS instance monitoring:
- Subscribe to alerts
- Respond when server is down (e.g. check logs, restart)

#### 2. New entry actions:
- Examine and approve for newly submitted entries by non-Admin users (rare)
- Check if heatmap and meta data for new entry is correct (should success)

#### 3. HTTPS certificate renewal:
- Due on _Sep 22 2018_

Things that should _NOT_ need care (done automatically):

- Indexing of all entries [triggered by CRUD]
- Image (thumbnail) and JSON meta for entries [triggered by CRUD]
- Tools repository update download [GitHub Webhook]
- Data/config backup [weekly on Sun morning by cron]

Keep an eye on them when fail (you get admin email notice)



> Should write complete docs/wiki like this: https://github.com/t47io/django-Primerize-server/wiki
