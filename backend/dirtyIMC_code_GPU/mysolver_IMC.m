%function [UUX, D, U] = biasfact(X, A, kx, ncluster, lambda, maxit, init_U, init_D, showopt)
function [U S V] = mysolver_IMC(A, X, Y, lambda, maxit, init_U, init_S, init_V, showopt)
A = gpuArray(A);
X = gpuArray(X);
Y = gpuArray(Y);

if ~exist('showopt')
	showopt = 0;
end

epsilon = 10^-2;
A = sparse(A);
[n1, d1] = size(X);
[n2, d2] = size(Y);
% check if feature is orthogonal, which is needed here.
% So UX, UY is the orthogonal features used for optimization.
testorth = norm(X'*X-eye(d1), 'fro');
if(testorth < 10^-7)
	UX = X;
else
	[UX, ~, ~] = svds(X, d1);
	fprintf('Warning: dist to eyes = %e, X is changed to be orthogonal.\n', testorth);
end
testorth = norm(Y'*Y-eye(d2), 'fro');
if(testorth < 10^-7)
	UY = Y;
else
	[UY, ~, ~] = svds(Y, d2);
	fprintf('Warning: dist to eyes = %e, Y is changed to be orthogonal.\n', testorth)
end

if exist('init_U') == 0 || exist('init_S') == 0 || exist('init_V') == 0
	U = gpuArray(zeros(d1, 1));
	S = gpuArray(zeros(1, 1));
	V = gpuArray(zeros(d2, 1));
else
	U = init_U;
	S = init_S;
	V = init_V;
end

[ii, jj, vv] = find(A);

try
    UX = gpuArray(UX);
    UY = gpuArray(UY);
	%R = CompResidual(A, UY', (UX*U*S*V')');
	entries = dotp((UX*U*S*V'), UY, ii, jj);
	R = A-sparse(ii, jj, entries, n1, n2);
	%norm(A-RR-R, 'fro')
	%pause;
	obj = (norm(R,'fro')^2)/2+lambda*sum(abs(diag(S)));
	if showopt ~= 0
		fprintf('init: %g\n', obj);
	end
	%norm(UX'*UX-eye(size(UX, 2)))
catch err
	fprintf('First iteration error\n')
	keyboard;
end

for iter = 1:maxit
	grad = -UX'*R*UY;
	t = 1;

	[tmp_U ss tmp_V] = svd(U*S*V'-t*grad);
    
	tmp_S = diag(max(diag(ss)-lambda, 0));
    
	%tmp_R = CompResidual(A, UY', (UX*tmp_U*tmp_S*tmp_V')');
	entries = dotp((UX*tmp_U*tmp_S*tmp_V'), UY, ii, jj);
	tmp_R = A-sparse(ii, jj, entries, n1, n2);
	%norm(A-RR-tmp_R, 'fro')
	%pause;
	tmp_obj = (norm(tmp_R,'fro')^2)/2+lambda*sum(abs(diag(tmp_S)));

	R = gpuArray(tmp_R);
	U = gpuArray(tmp_U); 
	S = gpuArray(tmp_S); 
	V = gpuArray(tmp_V);

	% stopping criterion
	if(tmp_obj > (1-epsilon)*obj)
		return;
	end
	obj = tmp_obj;

	if showopt ~= 0
		sym = norm(U*S*V' - V*S*U', 'fro');
		fprintf('Iter %g, obj = %g, symmetric = %g, t = %g, rank = %g\n', iter, obj, sym, t, nnz(diag(S)));
	end

end

