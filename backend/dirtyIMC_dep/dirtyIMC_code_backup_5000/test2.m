function [SN] = test2(X)
    size(X)
    XR = full(mmread("XR.mm.mtx"));
    YR = full(mmread("Y.mm.mtx"));
%     YR = full(mmread("sparseYactor.mm.mtx"));
%     YR = YR(:,1:200);
    M = full(mmread("M.mm.mtx"));

    TX = X/XR; %QR = N
    TX(isnan(TX)) = 0;
    TX(isinf(TX)) = 0;
    N = TX * M * YR'; %X * M * Y'
    [~,SN] = sort(N, 2, 'descend'); %sort for best 
    %SN = int8(SN);
    filename = strcat("SN",".mm.mtx");
    mmwrite(filename,SN);
end