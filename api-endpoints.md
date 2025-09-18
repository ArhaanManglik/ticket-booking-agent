    get/trains/list
    get/trains/{trainNumber}
    get/trains/{trainNumber}/schedule
    get/trains/{trainNumber}/instances
    get/trains/{trainNumber}/average-delay
    get/trains/all-kvs
    get/trains/between
    get/trains/live-map


## Get paginated train list​

Retrieves a paginated list of trains with filtering and search capabilities. Supports filtering by train type, railway zone, and text search across train numbers, names, and station codes.
Query Parameters

    page

Type: integer
min:  
1
default:  
1

Page number (1-based)
limit
Type: integer
min:  
1
max:  
100
default:  
50

Number of items per page (1-100)
type
Type: string

Filter by train type (case-insensitive)
zone
Type: string

Filter by railway zone (case-insensitive)
search
Type: string

Search in train number, name, or station codes

### output
{
  "success": true,
  "data": {
    "trains": [
      {
        "train_number": "12301",
        "train_name": "Howrah Rajdhani Express",
        "type": "RAJ",
        "zone": "ER",
        "source_station_code": "NDLS",
        "destination_station_code": "HWH",
        "distance_km": 1447,
        "avg_speed_kmph": 83.5
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 15000,
      "totalPages": 300,
      "hasNext": true,
      "hasPrev": false
    },
    "filters": {
      "type": "Express",
      "zone": "WR",
      "search": "rajdhani"
    }
  },
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

## Get comprehensive train data​

Retrieves comprehensive information about a specific train including static details, schedule, and optionally live tracking data.

Data Types:

    full: Complete train data with live information (default)
    static: Only database information without live data
    live: Only live tracking information wrapped in { liveData: ... }

Path Parameters

    trainNumber

Type: string
Pattern: ^\d{5}$
required

    5-digit train number

Query Parameters

    journeyDate

Type: stringFormat: date
Pattern: ^\d{4}-\d{2}-\d{2}$

Journey date in YYYY-MM-DD format
dataType
Type: stringenum
default:  
"full"

Type of data to retrieve

    full
    static
    live

provider
Type: stringenum
default:  
"railradar"

Data provider for live information

    railradar
    NTES

userId
Type: string

User ID for tracking (optional)

### output
{
  "success": true,
  "data": {
    "train": {
      "trainNumber": "12301",
      "trainName": "Howrah Rajdhani Express",
      "hindiName": "string",
      "type": "string",
      "zone": "string",
      "sourceStationCode": "NDLS",
      "sourceStationName": "New Delhi",
      "destinationStationCode": "HWH",
      "destinationStationName": "Howrah Junction",
      "runningDaysBitmap": 1,
      "...": "[Additional Properties Truncated]"
    },
    "route": [
      {
        "id": 1,
        "sequence": 1,
        "stationCode": "string",
        "stationName": "string",
        "isHalt": 1,
        "scheduledArrival": 1,
        "scheduledDeparture": 1,
        "haltDurationMinutes": 1,
        "platform": "string",
        "day": 1,
        "...": "[Additional Properties Truncated]"
      }
    ],
    "crossings": [
      {
        "id": 1,
        "stationCode": "string",
        "sequence": 1,
        "eventType": "string",
        "runningDaysBitmap": 1,
        "crossedTrainNumber": "string",
        "crossedTrainName": "string",
        "crossedTrainLink": "string"
      }
    ],
    "liveData": {
      "trainNumber": "string",
      "trainName": "string",
      "journeyDate": "2025-09-18",
      "lastUpdatedAt": "2025-09-18T14:57:13.382Z",
      "currentLocation": {
        "latitude": 1,
        "longitude": 1,
        "stationCode": "string",
        "status": "ARRIVED",
        "distanceFromOriginKm": 1,
        "distanceFromLastStationKm": 1
      },
      "overallDelayMinutes": 1,
      "dataSource": "string",
      "statusSummary": "string",
      "route": [
        {
          "station": {
            "code": "NDLS",
            "name": "New Delhi",
            "nameHindi": "string",
            "latitude": 1,
            "longitude": 1
          },
          "scheduledArrival": 1,
          "scheduledDeparture": 1,
          "actualArrival": 1,
          "actualDeparture": 1,
          "delayArrivalMinutes": 1,
          "delayDepartureMinutes": 1,
          "platform": "string",
          "distanceFromOriginKm": 1,
          "journeyDay": 1,
          "...": "[Additional Properties Truncated]"
        }
      ]
    },
    "statusSummary": "string",
    "liveDataError": {
      "code": "VALIDATION:INVALID_INPUT",
      "message": "string",
      "details": "string",
      "context": {
        "timestamp": "2025-09-18T14:57:13.382Z",
        "traceId": "string",
        "service": "string",
        "method": "string",
        "userId": "string",
        "requestId": "string",
        "validationErrors": {},
        "metadata": {}
      },
      "statusCode": 1,
      "retryable": true
    },
    "metadata": {
      "hasLiveData": true,
      "lastStaticUpdate": "2025-09-18T14:57:13.382Z",
      "lastLiveUpdate": "2025-09-18T14:57:13.382Z",
      "canRefreshLive": true,
      "journeyStatus": {}
    }
  },
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

## Get train schedule​

Retrieves the detailed schedule/route for a specific train on a given journey date
Path Parameters

    trainNumber

Type: string
Pattern: ^\d{5}$
required

    5-digit train number

Query Parameters

    journeyDate

Type: stringFormat: date
Pattern: ^\d{4}-\d{2}-\d{2}$
required

Journey date in YYYY-MM-DD format

### output
{
  "success": true,
  "data": {
    "train": {
      "number": "12301",
      "name": "Rajdhani Express",
      "type": "RAJ",
      "nameHindi": "string",
      "typeDescription": "string",
      "typeDescriptionHindi": "string",
      "source": {
        "code": "NDLS",
        "name": "New Delhi",
        "nameHindi": "string",
        "latitude": 1,
        "longitude": 1
      },
      "destination": {
        "code": "NDLS",
        "name": "New Delhi",
        "nameHindi": "string",
        "latitude": 1,
        "longitude": 1
      }
    },
    "travelTime": "string",
    "runDays": "string",
    "availableClasses": [
      "string"
    ],
    "validFrom": "string",
    "isReserved": true,
    "availableStartDates": [
      "2025-09-18"
    ],
    "route": [
      {
        "stopNumber": 1,
        "station": {
          "code": "NDLS",
          "name": "New Delhi",
          "nameHindi": "string",
          "latitude": 1,
          "longitude": 1
        },
        "distanceKilometers": 1,
        "journeyDay": 1,
        "isLocoReversal": true,
        "runDays": "string",
        "schedule": {
          "arrival": "string",
          "departure": "string",
          "haltMinutes": 1
        }
      }
    ]
  },
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

## Get train journey instances​

Retrieves past and future journey instances for a specific train. The response format depends on the selected provider.
Path Parameters

    trainNumber

Type: string
Pattern: ^\d{5}$
required

    5-digit train number

Query Parameters

    provider

Type: stringenum
default:  
"railradar"

Data provider for live information

    railradar
    NTES

### output
{
  "success": true,
  "data": [
    {
      "startDate": "2025-09-18",
      "departureTimestamp": 1,
      "status": "RUNNING",
      "positionSummary": "string",
      "exceptionMessage": "string"
    }
  ],
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

## Find trains between stations​

Finds all trains that run between two specified stations
Query Parameters

    from

Type: string
min length:  
1
max length:  
10
required

Source station code (1-10 characters, automatically converted to uppercase)
to
Type: string
min length:  
1
max length:  
10
required

Destination station code (1-10 characters, automatically converted to uppercase)

### output
{
  "success": true,
  "data": [
    {
      "trainNumber": "12301",
      "trainName": "Rajdhani Express",
      "sourceStationCode": "NDLS",
      "destinationStationCode": "HWH",
      "fromStationSchedule": {
        "arrivalMinutes": 1,
        "departureMinutes": 1,
        "day": 1,
        "platform": "string",
        "distanceFromSourceKm": 1
      },
      "toStationSchedule": {
        "arrivalMinutes": 1,
        "departureMinutes": 1,
        "day": 1,
        "platform": "string",
        "distanceFromSourceKm": 1
      }
    }
  ],
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

# STATIONS
Stations (Collapsed)​

Station-related operations including information and live boards
Stations Operations

    get/stations/{stationCode}/info
    get/stations/{stationCode}/live
    get/stations/all-kvs

## Get station information​

Retrieves static information about a specific station
Path Parameters

    stationCode

Type: string
min length:  
1
max length:  
10
required

Station code (1-10 characters, automatically converted to uppercase)

### OUTPUT 
{
  "success": true,
  "data": {
    "code": "NDLS",
    "name": "New Delhi",
    "nameHindi": "string",
    "latitude": 1,
    "longitude": 1
  },
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

## Get live station board​

Retrieves real-time departure and arrival information for a specific station
Path Parameters

    stationCode

Type: string
min length:  
1
max length:  
10
required

    Station code (1-10 characters, automatically converted to uppercase)

Query Parameters

    hours

Type: integer
min:  
1
max:  
8
default:  
8

Number of hours to look ahead (1-8)
toStationCode
Type: string
max length:  
10

Filter trains going to specific destination station (automatically converted to uppercase)

### Output
{
  "success": true,
  "data": {
    "station": {
      "code": "NDLS",
      "name": "New Delhi",
      "nameHindi": "string",
      "latitude": 1,
      "longitude": 1
    },
    "queryingForNextHours": 1,
    "totalTrains": 1,
    "trains": [
      {
        "train": {
          "number": "12301",
          "name": "Rajdhani Express",
          "type": "RAJ",
          "nameHindi": "string",
          "typeDescription": "string",
          "typeDescriptionHindi": "string",
          "source": {
            "code": "NDLS",
            "name": "New Delhi",
            "nameHindi": "string",
            "latitude": 1,
            "longitude": 1
          },
          "destination": {
            "code": "NDLS",
            "name": "New Delhi",
            "nameHindi": "string",
            "latitude": 1,
            "longitude": 1
          }
        },
        "platform": "string",
        "journeyDate": "2025-09-18",
        "schedule": {
          "arrival": "string",
          "departure": "string"
        },
        "live": {
          "expectedArrival": "string",
          "expectedDeparture": "string",
          "arrivalDelayDisplay": "string",
          "departureDelayDisplay": "string"
        },
        "status": {
          "isCancelled": true,
          "isDiverted": true,
          "isArrivalCancelled": true,
          "isDepartureCancelled": true,
          "hasArrived": true,
          "hasDeparted": true,
          "isDestinationChanged": true,
          "isSourceChanged": true
        },
        "coachInfo": {
          "arrivalCoachPosition": "string",
          "departureCoachPosition": "string"
        }
      }
    ]
  },
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

# Search (Collapsed)​

Search operations for trains and stations
Search Operations

    get/search/trains
    get/search/stations

## Search trains​

Search for trains by number or name
Query Parameters

    query

Type: string
min length:  
1
required

Search query (train number or name)

### OUTPUT 
{
  "success": true,
  "data": [
    {
      "trainNumber": "12301",
      "trainName": "Rajdhani Express",
      "sourceStationCode": "NDLS",
      "destinationStationCode": "HWH"
    }
  ],
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}

## Search stations​

Search for stations by code or name
Query Parameters

    query

Type: string
min length:  
1
required

Search query (station code or name)
provider
Type: stringenum
default:  
"railradar"

Data provider for search

    railradar
    NTES

### Output
{
  "success": true,
  "data": [
    {
      "code": "NDLS",
      "name": "New Delhi",
      "nameHindi": "string",
      "latitude": 1,
      "longitude": 1
    }
  ],
  "error": {
    "code": "VALIDATION:INVALID_INPUT",
    "message": "string",
    "details": "string",
    "context": {
      "timestamp": "2025-09-18T14:57:13.382Z",
      "traceId": "string",
      "service": "string",
      "method": "string",
      "userId": "string",
      "requestId": "string",
      "validationErrors": {},
      "metadata": {}
    },
    "statusCode": 1,
    "retryable": true
  },
  "meta": {
    "timestamp": "2025-09-18T14:57:13.382Z",
    "traceId": "string",
    "executionTime": 1,
    "service": "string",
    "method": "string"
  }
}
