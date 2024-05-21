/*
 *  Copyright (C) 2024 Callum Gran
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
#ifndef DATETIME_H
#define DATETIME_H

#include <stdint.h>

typedef struct datetime_t {
    uint16_t year;
    uint8_t month;
    uint8_t day;
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
    uint64_t nanosecond;
} DateTime;

int compare_datetime(const DateTime *const restrict a, const DateTime *const restrict b);

int parse_date_time(DateTime *restrict dt, char *const datestr);

void date_time_to_string(const DateTime *const restrict dt, char *restrict datestr);

#endif // DATETIME_H