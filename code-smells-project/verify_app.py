from app import create_app
app = create_app()
rules = [str(r) for r in app.url_map.iter_rules()]
print("APP OK")
print("Routes:", len(rules))
for r in sorted(rules):
    print(" ", r)
