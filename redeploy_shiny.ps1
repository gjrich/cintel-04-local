Write-Host "Clearing cached project files..."
shiny static-assets remove

Write-Host "Regenerating static assets..."
shinylive export penguins docs

Write-Host "Starting local server..."
py -m http.server --directory docs --bind localhost 8008
