#! /bin/sh
echo "Removing previous zip"
rm cba.zip
echo "Zipping project"
zip -r cba.zip *
echo "Publishing CBA"

curl --location --request POST 'localhost:8000/api/v1/blueprint-model/publish' \
--header 'Authorization: Basic Y2NzZGthcHBzOmNjc2RrYXBwcw==' \
--form 'file=@cba.zip' | python -m json.tool

echo "\n-----Done-----"


docker cp bp-rest:/opt/app/onap/config/application.properties .