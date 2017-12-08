function [sdcg] = dcg(rel,i)
%NDCG Summary of this function goes here
%   Detailed explanation goes here
     dcg = (rel)./(log2(i + 1));
     sdcg = sum(dcg,2);
end

