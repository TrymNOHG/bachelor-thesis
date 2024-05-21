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
#ifndef MACROS_H
#define MACROS_H

#include <datetime.h>
#include <stdint.h>
#include <stdlib.h>

#define EVAL0(...) __VA_ARGS__
#define EVAL1(...) EVAL0(EVAL0(EVAL0(__VA_ARGS__)))
#define EVAL2(...) EVAL1(EVAL1(EVAL1(__VA_ARGS__)))
#define EVAL3(...) EVAL2(EVAL2(EVAL2(__VA_ARGS__)))
#define EVAL4(...) EVAL3(EVAL3(EVAL3(__VA_ARGS__)))
#define EVAL(...) EVAL4(__VA_ARGS__)

#define NOP

#define MAP_POP_ONE_ARG0(F, X, ...) F(X) __VA_OPT__(MAP_POP_ONE_ARG1 NOP(F, __VA_ARGS__))
#define MAP_POP_ONE_ARG1(F, X, ...) F(X) __VA_OPT__(MAP_POP_ONE_ARG0 NOP(F, __VA_ARGS__))

#define MAP_ONE_ARG(F, ...) __VA_OPT__(EVAL(MAP_POP_ONE_ARG0(F, __VA_ARGS__)))

#define MAP_POP_TWO_ARGS0(F, X, Y, ...) F(X, Y) __VA_OPT__(MAP_POP_TWO_ARGS1 NOP(F, __VA_ARGS__))
#define MAP_POP_TWO_ARGS1(F, X, Y, ...) F(X, Y) __VA_OPT__(MAP_POP_TWO_ARGS0 NOP(F, __VA_ARGS__))

#define MAP_TWO_ARGS(F, ...) __VA_OPT__(EVAL(MAP_POP_TWO_ARGS0(F, __VA_ARGS__)))

uint8_t uint8_t_from_string(char *str)
{
    return (uint8_t)atoi(str);
}

uint16_t uint16_t_from_string(char *str)
{
    return (uint16_t)atoi(str);
}

int16_t int16_t_from_string(char *str)
{
    return (int16_t)atoi(str);
}

int64_t int64_t_from_string(char *str)
{
    return (int64_t)atoll(str);
}

uint64_t uint64_t_from_string(char *str)
{
    return (uint64_t)atoll(str);
}

double double_from_string(char *str)
{
    return atof(str);
}

#define GEN_FROM_STRING_LINE(struct_member_type, struct_member) \
    l_data[i]->struct_member = struct_member_type##_from_string(strtok_r(NULL, ",", &save_ptr));

#define GEN_LINE_PARSE_FUNC(struct_name, ...)                      \
    void parse_##struct_name##_line(char *line, void *data, int i) \
    {                                                              \
        struct_name **l_data = (struct_name **)data;               \
        char *save_ptr = NULL;                                     \
        char *date = strtok_r(line, ",", &save_ptr);               \
        parse_date_time(&l_data[i]->dt, date);                     \
        char *node_id = strtok_r(NULL, ",", &save_ptr);            \
        l_data[i]->node_id = atoi(node_id);                        \
        strtok_r(NULL, ",", &save_ptr);                            \
        MAP_TWO_ARGS(GEN_FROM_STRING_LINE, __VA_ARGS__)            \
    }

#define STRUCT_LINE(type, name) type name;

#define GEN_STRUCT(struct_name, ...)           \
    typedef struct {                           \
        DateTime dt;                           \
        uint16_t node_id;                      \
        MAP_TWO_ARGS(STRUCT_LINE, __VA_ARGS__) \
    } struct_name;                             \
    GEN_LINE_PARSE_FUNC(struct_name, __VA_ARGS__)

#define GEN_FUNCTION(func_name, struct_name, file_name, out_file_name, file_len, csv_header_line, \
                     parse_func, ...)                                                             \
    int func_name(NodeDownTimeLen *mode_data)                                                     \
    {                                                                                             \
        struct timespec start, end;                                                               \
        double elapsed = 0.0;                                                                     \
        clock_gettime(CLOCK_MONOTONIC_RAW, &start);                                               \
        const size_t file_size = file_len;                                                        \
        struct_name **arr = malloc(file_size * sizeof(struct_name *));                            \
        for (size_t i = 0; i < file_size; i++) {                                                  \
            arr[i] = malloc(sizeof(struct_name));                                                 \
        }                                                                                         \
        if (csv_parse_file(file_name, (void **)arr, parse_func) == 0) {                           \
            printf("Successfully parsed file %s!\n", file_name);                                  \
        } else {                                                                                  \
            fprintf(stderr, "Error parsing file %s :(!\n", file_name);                            \
            return 1;                                                                             \
        }                                                                                         \
        List out_list;                                                                            \
        list_init_prealloc(&out_list, sizeof(struct_name *), (int)(file_size * 0.8));             \
        filter_bad_times((void **)arr, mode_data, &out_list, file_size);                          \
        FILE *fp = fopen(out_file_name, "w");                                                     \
        if (!fp) {                                                                                \
            fprintf(stderr, "Error opening file with name %s!\n", out_file_name);                 \
            return 1;                                                                             \
        }                                                                                         \
        fprintf(fp, csv_header_line);                                                             \
        char date[50] = { 0 };                                                                    \
        for (size_t i = 0; i < out_list.size; i++) {                                              \
            struct_name **row = list_get(&out_list, i);                                           \
            date_time_to_string(&(*row)->dt, date);                                               \
            fprintf(fp, __VA_ARGS__);                                                             \
        }                                                                                         \
        fclose(fp);                                                                               \
        for (size_t i = 0; i < file_size; i++) {                                                  \
            free(arr[i]);                                                                         \
        }                                                                                         \
        free(arr);                                                                                \
        clock_gettime(CLOCK_MONOTONIC_RAW, &end);                                                 \
        elapsed = (end.tv_sec - start.tv_sec);                                                    \
        elapsed += (end.tv_nsec - start.tv_nsec) / 1000000000.0;                                  \
        printf("----------------------------------\n");                                           \
        printf("Time used to parse and filter %s: %f s \n", file_name, elapsed);                  \
        printf("----------------------------------\n");                                           \
        return 0;                                                                                 \
    }

#endif // MACROS_H