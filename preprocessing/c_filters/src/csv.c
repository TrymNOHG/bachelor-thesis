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
#include <csv.h>
#include <datetime.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

int qsort_cmp(const void *a, const void *b)
{
    return ((ModeEventData *)a)->node_id - ((ModeEventData *)b)->node_id;
}

int csv_parse_file(const char *const filename, void **data, parse_func_t parse_func)
{
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        fprintf(stderr, "Error opening file with name %s!\n", filename);
        return 1;
    }

    ssize_t read = 0;
    char *line;
    size_t len = 0;
    int i = 0;
    bool first = true;

    while ((read = getline(&line, &len, fp)) != -1) {
        if (first) {
            first = false;
            continue;
        }

        if (line) {
            parse_func(line, data, i);
            i++;
        }
    }

    free(line);
    fclose(fp);

    return 0;
}

NodeDownTimeLen *parse_mode_file()
{
    FILE *fp = fopen(MODE_FILENAME, "r");
    if (!fp) {
        fprintf(stderr, "Error opening file with name %s!\n", MODE_FILENAME);
        return NULL;
    }

    ModeEventData mode_arr[MODE_LINES_IN_FILE] = { 0 };

    ssize_t read = 0;
    char *line;
    size_t len = 0;
    int i = 0;
    bool first = true;

    while ((read = getline(&line, &len, fp)) != -1) {
        if (first) {
            first = false;
            continue;
        }

        if (line) {
            char *save_ptr = NULL;
            char *date = strtok_r(line, ",", &save_ptr);
            parse_date_time(&mode_arr[i].dt, date);

            char *node_id = strtok_r(NULL, ",", &save_ptr);
            mode_arr[i].node_id = atoi(node_id);

            strtok_r(NULL, ",", &save_ptr);

            char *mode = strtok_r(NULL, ",", &save_ptr);
            mode_arr[i].mode = atoi(mode);
            i++;
        }
    }

    free(line);

    qsort(mode_arr, MODE_LINES_IN_FILE, sizeof(ModeEventData), qsort_cmp);

    i = 0;

    NodeDownTime **arr = malloc((MODE_LINES_IN_FILE + 1 / 2) * sizeof(NodeDownTime *));
    for (int j = 0; j < (MODE_LINES_IN_FILE + 1 / 2); j++) {
        arr[j] = malloc(sizeof(NodeDownTime));
    }

    for (int j = 0; j < MODE_LINES_IN_FILE; j++) {
        if (mode_arr[j].mode == 0) {
            for (int k = j + 1; k < MODE_LINES_IN_FILE; k++) {
                if (mode_arr[k].mode == 6 && mode_arr[j].node_id == mode_arr[k].node_id) {
                    arr[i]->start_dt = mode_arr[j].dt;
                    arr[i]->end_dt = mode_arr[k].dt;
                    arr[i]->node_id = mode_arr[k].node_id;
                    i++;
                    break;
                }
            }
        }
    }

    NodeDownTimeLen *ret = malloc(sizeof(NodeDownTimeLen));
    ret->len = i;
    ret->arr = arr;

    return ret;
}