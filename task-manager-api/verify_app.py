from app import app
rules = [str(r) for r in app.url_map.iter_rules()]
print("APP OK")
print(f"Routes: {len(rules)}")
for r in sorted(rules):
    print(f"  {r}")
