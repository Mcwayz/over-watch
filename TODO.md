# Task: Remove React Frontend - Keep Backend + Swagger

## Steps:\n- [x] 1. Delete entire `frontend/` directory ✓\n- [x] 2. Update `over_watch/settings.py`: Remove \"http://localhost:3000\" from CORS_ALLOWED_ORIGINS ✓\n- [x] 3. Update `over_watch/settings_fixed.py`: Same as step 2 ✓\n- [x] 4. Update `README.md`: Remove frontend setup/tech stack sections ✓\n- [x] 5. Review `.gitignore`: Node ignores already present, good ✓\n- [ ] 6. Run `python manage.py collectstatic --noinput --clear`\n- [ ] 7. Test: `python manage.py runserver` then visit http://localhost:8000/api/docs/`

**Current progress: Settings done, updating README next**
