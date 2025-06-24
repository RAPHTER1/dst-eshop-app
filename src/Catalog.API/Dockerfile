FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app

COPY . .

WORKDIR /app/src/Catalog.API
RUN dotnet restore

RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime

WORKDIR /app

COPY --from=build /app/src/Catalog.API/out ./

ENTRYPOINT ["dotnet", "Catalog.API.dll"]