
echo "Running isort..."
isort --settings-file ./.isort.cfg .

echo "Running black..."
black --config ./.black .

echo "Running flake8..."
flake8 --config .flake8 .

echo "All done!"