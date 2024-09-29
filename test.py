from datetime import datetime
diff = datetime.now() - datetime(2024, 9, 28, 0, 0, 0)
diff_in_s = diff.total_seconds()
hours = divmod(diff_in_s, 3600)[0]
print(hours)