FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app
LABEL maintainer="raphter"
LABEL version="1.0"
LABEL description="Basket.API for eShopOnContainers"

COPY . .

WORKDIR /app/src/Basket.API
RUN dotnet restore

RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime

WORKDIR /app

COPY --from=build /app/src/Basket.API/out ./

ENTRYPOINT ["dotnet", "Basket.API.dll"]