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
#ifndef CSV_H
#define CSV_H

#include <datatype.h>
#include <stdbool.h>

#define MODE_LINES_IN_FILE 42044
#define MODE_FILENAME "operator/metadata_mode_events.csv"

typedef void (*parse_func_t)(char *line, void *data, int i);

NodeDownTimeLen *parse_mode_file();

int csv_parse_file(const char *const filename, void **data, parse_func_t parse_func);

#endif // CSV_H