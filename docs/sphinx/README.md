Update-HTML:
```
sphinx-build -M html source/ build/ -a
```

Update-API-DOC:
```
sphinx-apidoc -o source/ ../../hybrid_grounding -e
```

Start-LOCAL Development Server:
```
python -m http.server
```

