# Golf Data Helper Lambda

> This repo contains python code for the purpose of making an API call to the Golf Leaderboard API to retrieve up to date data on a given Golf Tournament and publishing that data as a JSON file to an S3 bucket

## Architecture

This is a basic Lambda that will be scheduled using cron jobs (Amazon Cloudwatch Event) to run the python script to make a GET request to 