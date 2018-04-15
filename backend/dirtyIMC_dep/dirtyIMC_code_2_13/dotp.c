/*
 * dotp.c
 *
 * Compute the inner product between the corresponding row of two
 * matrices, where the index of rows are given in I and J column
 * vector. The result will be a column vector.
 *
 * The calling syntax:
 *       [o] = dotp(A, B, I, J)
 *
 * This is a MEX-file for MATLAB.
 *
 * Copyright 2008 Wei Tang (wtang@cs.utexas.edu)
 */

#include "mex.h"

/* The gateway function */
void mexFunction(int nlhs, mxArray *plhs[],
                 int nrhs, const mxArray *prhs[])
{
    if (nrhs < 4) {
        mexErrMsgTxt("dotp needs four input arguments!\n");
    }
    if (mxIsSparse(prhs[0]) || mxIsSparse(prhs[1])) {
		mexErrMsgTxt("Input matrix should be dense matrix!\n");
	}
	size_t Ma = mxGetM(prhs[0]), Mb = mxGetM(prhs[1]), N = mxGetN(prhs[0]), L = mxGetM(prhs[2]);
	if (N != mxGetN(prhs[1])) {
		mexErrMsgTxt("Input matrices A and B should have the same number of columns!\n");
	}
    if (L != mxGetM(prhs[3]) || mxGetN(prhs[2]) != mxGetN(prhs[3])
        || mxGetN(prhs[2]) != 1) {
        mexErrMsgTxt("Input vectors I and J should have the same length!\n");
    }

    double *aPr = mxGetPr(prhs[0]);
    double *bPr = mxGetPr(prhs[1]);
    double *iPr = mxGetPr(prhs[2]);
    double *jPr = mxGetPr(prhs[3]);
    plhs[0] = mxCreateDoubleMatrix(L,1,mxREAL);
    double* oPr = mxGetPr(plhs[0]);
	size_t i, j;
	for (i = 0; i < L; i++) {
		oPr[i] = 0.0;
		for (j = 0; j < N; j++) {
			oPr[i] += aPr[j*Ma+(size_t)iPr[i]-1]*bPr[j*Mb+(size_t)jPr[i]-1];
		}
	}	
}
