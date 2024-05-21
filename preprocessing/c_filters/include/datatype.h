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
#ifndef DATATYPE_H
#define DATATYPE_H

/* Note that as all data processed is from service_id 2, I just don't save it! */

#include <stdbool.h>
#include <stdint.h>

#include <datetime.h>
#include <lib/list.h>

typedef struct mode_event_data_t {
    DateTime dt;
    uint16_t node_id;
    uint8_t mode;
} ModeEventData;

typedef struct node_down_time_t {
    DateTime start_dt;
    DateTime end_dt;
    uint16_t node_id;
} NodeDownTime;

typedef struct node_down_time_len_t {
    uint32_t len;
    NodeDownTime **arr;
} NodeDownTimeLen;

typedef struct abstract_data_t {
    DateTime dt;
    uint16_t node_id;
} AbstractData;

typedef struct filter_thread_data_t {
    uint16_t start;
    uint16_t end;
    size_t len;
    void **data;
    NodeDownTimeLen *dt_data;
    List *new_rows;
} FilterThreadData;

#endif // DATATYPE_H