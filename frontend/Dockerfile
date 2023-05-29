FROM node:18.16-alpine AS build

COPY . /frontend
WORKDIR /frontend

RUN npm install
RUN npm run build

FROM nginx:latest
COPY --from=build /frontend/dist/frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
