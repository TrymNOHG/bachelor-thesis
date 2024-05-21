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
#include <datetime.h>
#include <stdio.h>

int compare_datetime(const DateTime *const restrict a, const DateTime *const restrict b)
{
    if (a->year == b->year) {
        if (a->month == b->month) {
            if (a->day == b->day) {
                if (a->hour == b->hour) {
                    if (a->minute == b->minute) {
                        if (a->second == b->second) {
                            return a->nanosecond - b->nanosecond;
                        } else {
                            return a->second - b->second;
                        }
                    } else {
                        return a->minute - b->minute;
                    }
                } else {
                    return a->hour - b->hour;
                }
            } else {
                return a->day - b->day;
            }
        } else {
            return a->month - b->month;
        }
    } else {
        return a->year - b->year;
    }
}

int parse_date_time(DateTime *restrict dt, char *const datestr)
{
    return sscanf(datestr, "%hd-%hhd-%hhd %hhd:%hhd:%hhd.%ld", &dt->year, &dt->month, &dt->day,
                  &dt->hour, &dt->minute, &dt->second, &dt->nanosecond);
}

void date_time_to_string(const DateTime *const restrict dt, char *restrict datestr)
{
    snprintf(datestr, 50, "%02d-%02d-%02d %02d:%02d:%02d.%05lu", dt->year, dt->month, dt->day,
             dt->hour, dt->minute, dt->second, dt->nanosecond);
}