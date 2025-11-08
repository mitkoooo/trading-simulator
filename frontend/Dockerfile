FROM oven/bun:1 AS base
COPY ./package.json ./bun.lock /app/
WORKDIR /app
RUN bun install --frozen-lockfile

# For development:
FROM base AS development 
WORKDIR /app
COPY . .   
ENV VITE_DEV_HOST=0.0.0.0
ENV VITE_DEV_PORT=3000
EXPOSE 3000
CMD ["bun",  "run", "dev"]

# Production build stage
FROM base AS build
WORKDIR /app
COPY . .
RUN bun build

# Production stage
FROM oven/bun:1-alpine AS production
WORKDIR /app
RUN bun global add serve
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["bunx", "serve", "-s", "dist", "-l", "3000"]
