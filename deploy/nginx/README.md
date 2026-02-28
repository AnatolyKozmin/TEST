## Nginx (prod)

This container expects certificates mounted to:

- `/etc/nginx/certs/fullchain.crt`
- `/etc/nginx/certs/privkey.key`

And will proxy:

- `/` -> `frontend:80`
- `/api/*` -> `backend:8000/api/*`

