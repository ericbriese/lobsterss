lobsterss
=========

[lobsterss](https://lobsterss.org/) serves up customisable lobste.rs RSS feeds

Todo:

- [ ] Fetch multiple pages
- [ ] Configurable search in url and desc
- [ ] json output
- [ ] Always link to lobste.rs comments instead of outbound link

Self-hosting
------------

With Compose:

```yaml
services:
  lobsterss:
    image: ghcr.io/ericbriese/lobsterss:latest
    container_name: lobsterss
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Then open `http://localhost:8000`.

To build the image yourself instead:

```bash
git clone https://github.com/ericbriese/lobsterss
cd lobsterss
docker build -t lobsterss .
docker run -p 8000:8000 lobsterss
```

License
-------

[MIT](LICENSE)
