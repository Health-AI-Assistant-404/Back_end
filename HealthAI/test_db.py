import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",  # طبق URI در پنل
        user="root",
        password="9RSaIdj00qgSV95VavQ0kdWy",
        host="manaslu.liara.cloud",
        port="33485"
    )
    print("✅ اتصال موفق شد")
    conn.close()
except Exception as e:
    print("❌ خطا در اتصال:", e)
