
n = 200;
k = 20;
rand('seed', 0);
randn('seed', 0);
sparsity = 0.25
feature_perturb = 0.3
m = ceil(n^2*sparsity); % sparsity
dim = 2*k;

% create a real low rank matrix L 
Tmp = randn(n, k);
Tmp2 = randn(n, k);

% Tmp = randi([0 1], n, k);
% Tmp2 = randi([0 1], n, k);
L = Tmp*Tmp2';

% optX/optY is the good feature space
[X, ~] = qr(Tmp);
Xorth = X(:,dim+1:end);
optX = X(:,1:dim);
[Y, ~] = qr(Tmp2);
Yorth = Y(:, dim+1:end);
optY = Y(:,1:dim);

ii = ceil(rand(m, 1)*n);
jj = ceil(rand(m, 1)*n);
ind = sparse(ii, jj, 1, n, n);
Obs = L.*(ind > 0);
real_sparsity = nnz(Obs)/(n^2);

% Perturb feature X and Y
replace_dim = ceil(feature_perturb*k);
X = optX;
X(:,1:replace_dim) = Xorth(:,1:replace_dim);
Y = optY;
Y(:,1:replace_dim) = Yorth(:, 1:replace_dim);

Obs = mmread("sparseN.mm.mtx")';
ObsU = Obs(1:200, 1:200);

fprintf('L1\tL2\tErr\tRank(M)\tRank(N)\n')
loss = inf;
lambda = [10^-3 10^-2 10^-1 1];
lambda1 = [1000000000];
for a = 1:length(lambda)	% parameter selection
	for b = 1:length(lambda1)
		[UU SS VV U S V] = dirtyIMC(ObsU, X, Y, lambda(a), lambda1(b));
		Completed = U*S*V'+X*UU*SS*VV'*Y';
        M = UU*SS*VV';
 		l = norm(Completed-L, 'fro')/norm(L, 'fro');
 		fprintf('%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n', lambda(a), lambda1(b), l, rank(SS), rank(S));
		if(l < loss)
			loss = l;
		end
	end
end
fprintf('dirtyIMC: \tloss = %f\n\n', loss)

