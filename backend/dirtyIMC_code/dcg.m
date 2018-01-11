function [sdcg] = dcg(rel,i)
%NDCG Summary of this function goes here
%   Detailed explanation goes here
     dcg = (rel)./(log2(i + 1));
     dcg(isnan(dcg))=0; dcg(isinf(dcg))=0;
     sdcg = sum(dcg,2);
end

