FROM node:20-alpine

WORKDIR /app

# Флаги ускоряют установку: пропуск аудита, fund-сообщений, использование локального кэша
ENV NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_LOGLEVEL=warn

COPY package.json package-lock.json* ./

# Если package-lock.json есть — используем npm ci (быстрее и детерминированнее).
# Иначе fallback на npm install.
RUN if [ -f package-lock.json ]; then \
      npm ci --prefer-offline --no-audit --no-fund ; \
    else \
      npm install --no-audit --no-fund ; \
    fi

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
