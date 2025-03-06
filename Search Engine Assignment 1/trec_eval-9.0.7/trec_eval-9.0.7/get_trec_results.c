/* 
   Copyright (c) 2008 - Chris Buckley. 

   Permission is granted for use and modification of this file for
   research, non-commercial purposes. 
*/

#include "common.h"
#include "sysfunc.h"
#include "trec_eval.h"
#include "trec_format.h"
#include <ctype.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int te_get_trec_results_cleanup ();

/* Temp structure for values in input line */
typedef struct {
    char *qid;
    char *docno;
    char *sim;
} LINES;

static int parse_results_line(char **start_ptr, char **qid_ptr,
                              char **docno_ptr, char **sim_ptr,
                              char **run_id_ptr);
static int comp_lines_qid_docno();

static char *trec_results_buf = NULL;
static TEXT_RESULTS_INFO *text_info_pool = NULL;
static TEXT_RESULTS *text_results_pool = NULL;
static RESULTS *q_results_pool = NULL;

int te_get_trec_results(EPI *epi, char *text_results_file, ALL_RESULTS *all_results) {
    FILE *file;
    size_t size;
    char *ptr;
    char *current_qid;
    long i;
    LINES *lines;
    LINES *line_ptr;
    size_t num_lines;
    long num_qid;
    char *run_id_ptr = NULL;
    RESULTS *q_results_ptr;
    TEXT_RESULTS_INFO *text_info_ptr;
    TEXT_RESULTS *text_results_ptr;

    file = fopen(text_results_file, "rb");
    if (!file) {
        fprintf(stderr, "trec_eval.get_results: Cannot read results file '%s'\n", text_results_file);
        return (UNDEF);
    }
    
    fseek(file, 0, SEEK_END);
    size = ftell(file);
    rewind(file);

    trec_results_buf = (char *)malloc(size + 2);
    if (!trec_results_buf) {
        fprintf(stderr, "trec_eval.get_results: Cannot allocate memory for file '%s'\n", text_results_file);
        fclose(file);
        return (UNDEF);
    }
    
    fread(trec_results_buf, 1, size, file);
    fclose(file);
    
    if (trec_results_buf[size - 1] != '\n') {
        trec_results_buf[size] = '\n';
        size++;
    }
    trec_results_buf[size] = '\0';

    num_lines = 0;
    for (ptr = trec_results_buf; *ptr; ptr = strchr(ptr, '\n') + 1)
        num_lines++;

    lines = (LINES *)malloc(num_lines * sizeof(LINES));
    if (!lines) return (UNDEF);

    line_ptr = lines;
    ptr = trec_results_buf;
    while (*ptr) {
        while (*ptr && *ptr != '\n' && isspace(*ptr)) ptr++;
        if (*ptr == '\n') {
            ptr++;
            continue;
        }
        if (UNDEF == parse_results_line(&ptr, &line_ptr->qid, &line_ptr->docno,
                                        &line_ptr->sim, &run_id_ptr)) {
            fprintf(stderr, "trec_eval.get_results: Malformed line %ld\n",
                    (long)(line_ptr - lines + 1));
            return (UNDEF);
        }
        line_ptr++;
    }
    num_lines = line_ptr - lines;
    qsort((char *)lines, (int)num_lines, sizeof(LINES), comp_lines_qid_docno);
    
    num_qid = 1;
    for (i = 1; i < num_lines; i++) {
        if (strcmp(lines[i - 1].qid, lines[i].qid))
            num_qid++;
    }
    
    q_results_pool = (RESULTS *)malloc(num_qid * sizeof(RESULTS));
    text_info_pool = (TEXT_RESULTS_INFO *)malloc(num_qid * sizeof(TEXT_RESULTS_INFO));
    text_results_pool = (TEXT_RESULTS *)malloc(num_lines * sizeof(TEXT_RESULTS));
    if (!q_results_pool || !text_info_pool || !text_results_pool) return (UNDEF);
    
    q_results_ptr = q_results_pool;
    text_info_ptr = text_info_pool;
    text_results_ptr = text_results_pool;
    
    current_qid = "";
    for (i = 0; i < num_lines; i++) {
        if (strcmp(current_qid, lines[i].qid)) {
            if (i != 0) {
                text_info_ptr->num_text_results = text_results_ptr - text_info_ptr->text_results;
                text_info_ptr++;
                q_results_ptr++;
            }
            current_qid = lines[i].qid;
            text_info_ptr->text_results = text_results_ptr;
            *q_results_ptr = (RESULTS){current_qid, run_id_ptr, "trec_results", text_info_ptr};
        }
        text_results_ptr->docno = lines[i].docno;
        text_results_ptr->sim = atof(lines[i].sim);
        text_results_ptr++;
    }
    text_info_ptr->num_text_results = text_results_ptr - text_info_ptr->text_results;

    all_results->num_q_results = num_qid;
    all_results->results = q_results_pool;

    free(lines);
    return (1);
}

static int comp_lines_qid_docno(LINES *ptr1, LINES *ptr2) {
    int cmp = strcmp(ptr1->qid, ptr2->qid);
    if (cmp) return (cmp);
    return (strcmp(ptr1->docno, ptr2->docno));
}

static int parse_results_line(char **start_ptr, char **qid_ptr, char **docno_ptr,
                              char **sim_ptr, char **run_id_ptr) {
    char *ptr = *start_ptr;

    *qid_ptr = ptr;
    while (!isspace(*ptr)) ptr++;
    if (*ptr == '\n') return (UNDEF);
    *ptr++ = '\0';
    while (*ptr != '\n' && isspace(*ptr)) ptr++;
    while (!isspace(*ptr)) ptr++;
    if (*ptr++ == '\n') return (UNDEF);
    while (*ptr != '\n' && isspace(*ptr)) ptr++;
    *docno_ptr = ptr;
    while (!isspace(*ptr)) ptr++;
    if (*ptr == '\n') return (UNDEF);
    *ptr++ = '\0';
    while (*ptr != '\n' && isspace(*ptr)) ptr++;
    while (!isspace(*ptr)) ptr++;
    if (*ptr++ == '\n') return (UNDEF);
    while (*ptr != '\n' && isspace(*ptr)) ptr++;
    *sim_ptr = ptr;
    while (!isspace(*ptr)) ptr++;
    if (*ptr == '\n') return (UNDEF);
    *ptr++ = '\0';
    while (*ptr != '\n' && isspace(*ptr)) ptr++;
    if (*ptr == '\n') return (UNDEF);
    *run_id_ptr = ptr;
    while (!isspace(*ptr)) ptr++;
    if (*ptr != '\n') {
        *ptr++ = '\0';
        while (*ptr != '\n') ptr++;
    }
    *ptr++ = '\0';
    *start_ptr = ptr;
    return (0);
}

int te_get_trec_results_cleanup() {
    return 1;  // Modify to properly free memory if necessary
}

