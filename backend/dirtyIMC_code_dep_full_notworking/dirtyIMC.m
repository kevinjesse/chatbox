% M = UU*SS*VV', N = U*S*V', model = XMY^T + N

function [UU SS VV U S V] = dirtyIMC(A, X, Y, lambda, lambda1, maxit, showopt)
	if ~exist('maxit')
		maxit = 5;
	end
	if ~exist('showopt')
		showopt = 0;
	end
	
	[ii jj vv] = find(A);
	[n1, d1] = size(X);
	[n2, d2] = size(Y);
	if(size(A, 1) ~= n1 || size(A, 2) ~= n2)
		error('Dimensionality between observations and features does not match\n');
	end

	% M = UU*DD*UU'
	UU = zeros(d1, 1);
	SS = zeros(1, 1);
	VV = zeros(d2, 1);

	% N = U*S*V'
	U = zeros(n1, 1);
	S = zeros(1, 1);
	V = zeros(n2, 1);

	for i = 1:maxit

		% fix N, solve M with IMC
		if(showopt ~= 0)
			fprintf('Iteration %d:\n', i);
			fprintf('\tFix N, solve M with IMC...\t');
		end
		entries = vv - dotp(U*S, V, ii, jj);
		A = sparse(ii, jj, entries, n1, n2);
		[UU SS VV] = mysolver_IMC(A, X, Y, lambda, 5, UU, SS, VV, 0);

		obj = sum((vv-dotp(U*S, V, ii, jj)+dotp(X*UU*SS*VV', Y, ii, jj)).^2)/2 + lambda*sum(diag(SS))+lambda1*sum(diag(S));
		if(showopt ~= 0)
			fprintf('Objective = %e\n', obj);
		end

		% fix M, solve N with nuclear norm minimization
		if(showopt ~= 0)
			fprintf('\tFix M, solve N with MC...\t');
		end
		entries = vv - dotp(X*UU*SS*VV', Y, ii, jj);
		B = sparse(ii, jj, entries, n1, n2);
		[U S V] = mysolver_alt(B, lambda1, [], min(d1, d2), 5, U, S, V, 0);

		obj = sum((vv-dotp(U*S, V, ii, jj)+dotp(X*UU*SS*VV', Y, ii, jj)).^2)/2 + lambda*sum(diag(SS))+lambda1*sum(diag(S));
		if(showopt ~= 0)
			fprintf('Objective = %e\n', obj);
		end

	end

end
