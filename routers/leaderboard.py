# routers/leaderboard.py
import aiomysql
import mysql.connector
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from dependencies import DATABASE_CONFIG, create_db_connection
from models import LeaderboardEntry
from logging import Logger

router = APIRouter()

# Example SQL queries (using placeholders for dynamic values)
CURRENT_WEEK_LEADERBOARD_QUERY = (
    "SELECT * FROM leaderboard "
    "WHERE timestamp >= %(start_of_current_week)s "
    "ORDER BY score DESC"
)

LAST_WEEK_LEADERBOARD_QUERY = (
    "SELECT * FROM leaderboard "
    "WHERE timestamp >= %(start_of_last_week)s "
    "AND timestamp < %(start_of_current_week)s "
    "AND country = %(user_country)s "
    "ORDER BY score DESC LIMIT 200"
)



USER_RANK_QUERY = (
"SELECT UID, Name, Score, Country, TimeStamp,"
       "(SELECT COUNT(DISTINCT Score) + 1 "
        "FROM leaderboard AS l2 " 
        "WHERE l2.Score > l1.Score OR (l2.Score = l1.Score AND l2.TimeStamp < l1.TimeStamp)) AS UserRank "
"FROM leaderboard AS l1 "
"WHERE UID = %(user_id)s;"
)

DISTINCT_COUNTRIES_QUERY = "SELECT DISTINCT Country FROM leaderboard"



router = APIRouter()

@router.get('/api/main_leaderboard', response_model=List[LeaderboardEntry])
async def main_leaderboard(db: aiomysql.Connection = Depends(create_db_connection)):
    try:
        # Add your SQL query to fetch the leaderboard data here
        # For example, you can fetch the top N entries
        leaderboard_query = "SELECT * FROM leaderboard ORDER BY score DESC LIMIT 100"

        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(leaderboard_query)
            results = await cursor.fetchall()

        leaderboard_entries = []
        for result in results:
            timestamp_str = result['TimeStamp'].isoformat()
            leaderboard_entry = LeaderboardEntry(
                UID=result['UID'],
                Name=result['Name'],
                Score=result['Score'],
                Country=result['Country'],
                TimeStamp=timestamp_str
            )
            leaderboard_entries.append(leaderboard_entry)
        
        # Logger.debug("Number of entries sent: ", len(leaderboard_entries))
        return leaderboard_entries
    except Exception as e:
        print(f"Error in main_leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# API to display current week leaderboard
@router.get('/api/current_week_leaderboard', response_model=List[LeaderboardEntry])
async def current_week_leaderboard(db: aiomysql.Connection = Depends(create_db_connection)):
    try:
        start_of_current_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        params = {"start_of_current_week": start_of_current_week}
        
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(CURRENT_WEEK_LEADERBOARD_QUERY, params)
            results = await cursor.fetchall()

        leaderboard_entries = []
        for result in results:
            # Convert datetime to string using isoformat()
            timestamp_str = result['TimeStamp'].isoformat()

            # Ensure that the database column names match the model field names
            leaderboard_entry = LeaderboardEntry(
                UID=result['UID'],
                Name=result['Name'],
                Score=result['Score'],
                Country=result['Country'],
                TimeStamp=timestamp_str
            )
            leaderboard_entries.append(leaderboard_entry)
        print("Number of players returned to leaderboard:- ", len(leaderboard_entries))
        return leaderboard_entries
    except Exception as e:
        # Log the exception or print it for debugging
        print(f"Error in current_week_leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# API to display last week leaderboard by country
@router.get('/api/{country}', response_model=List[LeaderboardEntry])
async def last_week_leaderboard(country: str, db: aiomysql.Connection = Depends(create_db_connection)):
    try:
        start_of_last_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday() + 7)
        start_of_current_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        params = {"start_of_last_week": start_of_last_week, "start_of_current_week": start_of_current_week, "user_country": country}
        
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(LAST_WEEK_LEADERBOARD_QUERY, params)
            results = await cursor.fetchall()

        print("Country selected: ", country)
        # Print the results for debugging
        print("Print number of rows:", len(results))

        leaderboard_entries = []
        for result in results:
            # Convert datetime to string using isoformat()
            timestamp_str = result['TimeStamp'].isoformat()

            # Ensure that the 'Score' field is included in each entry
            leaderboard_entry = LeaderboardEntry(
                UID=result['UID'],
                Name=result['Name'],
                Score=result['Score'],
                Country=result['Country'],
                TimeStamp=timestamp_str
            )
            leaderboard_entries.append(leaderboard_entry)

        return leaderboard_entries
    except Exception as e:
        # Log the exception or print it for debugging
        print(f"Error in last_week_leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get('/api/countries', response_model=List[str])
async def get_distinct_countries(db: aiomysql.Connection = Depends(create_db_connection)):
    print("in")
    
    Logger.info("in")
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()
    cursor.execute(DISTINCT_COUNTRIES_QUERY)
    results = cursor.fetchall()

    new_res = []
    # Print the distinct countries
    for result in results:
        print(new_res.append(result[0]))

    print("Countries number of rows:", len(results))
    # distinct_countries = [result['Country'] for result in results if result['Country']]  # Filter out None values
    # print(distinct_countries)

    return ["new_res"]
    # except Exception as e:
    #     # Log the exception or print it for debugging
    #     print(f"Error in get_distinct_countries: {e}")
    #     raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get('/api/user_rank/{user_id}', response_model=int)
async def user_rank(user_id: str, db: aiomysql.Connection = Depends(create_db_connection)):
    try:
        params = {"user_id": user_id}
        
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(USER_RANK_QUERY, params)
            result = await cursor.fetchone()

        if result:
            return result["UserRank"]
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        # Log the exception or print it for debugging
        print(f"Error in user_rank: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")