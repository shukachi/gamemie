Как другие пользователи создают свои ветки от prod:

  Каждый разработчик у себя делает:
  git clone https://github.com/shukachi/gamemie.git
  cd gamemie
  git checkout -b vasya-developer origin/prod

  Работает в своей ветке, потом пушит:
  git push origin vasya-developer

  И создаёт Pull Request: vasya-developer → prod.

  git clone https://github.com/shukachi/gamemie.git
  cd gamemie
  git checkout -b vasya-developer origin/prod

  Работает в своей ветке, потом пушит:
  git push origin vasya-developer

  И создаёт Pull Request: vasya-developer → prod.

  ---
  Рекомендуемая схема веток:

  prod          ← стабильный релиз, только через PR
    └── dima-developer    ← твоя рабочая ветка
    └── vasya-developer   ← ветка другого разработчика
    └── petya-developer   ← и т.д.