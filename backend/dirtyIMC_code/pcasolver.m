function [approximationXRank] = pca(sparse, rank, size)
%PCA Summary of this function goes here
%   Detailed explanation goes here

    [coeff, score, latent, tsquared, explained, mu] = pca(sparse);
    approximationXRank = score(:,1:rank) * coeff(:,1:rank)' + repmat(mu, size, 1);

end

