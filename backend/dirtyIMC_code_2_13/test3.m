function [SN] = test3(X)
    XR = full(mmread("XR.mm.mtx"));
    YR = full(mmread("YR.mm.mtx"));
    M = full(mmread("M.mm.mtx"));

    TX = X/XR; %QR = N
    size(TX)
    size(YR')
    N = TX * M * YR'; %X * M * Y'
    [~,SN] = sort(N, 2, 'descend'); %sort for best 
    filename = strcat("SN",".mm.mtx");
    mmwrite(filename,SN);
end