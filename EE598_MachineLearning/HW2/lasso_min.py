for n_iter in range(max_iter):
	for ii in range(n_features):  # Loop over coordinates

		w_ii = w[ii]  # Store previous value
		#update residuals array R
		if w_ii != 0.0:
			# R += w_ii * X[:,ii]
			axpy(n_samples, w_ii, &X[0, ii], 1, &R[0], 1)

		# tmp = (X[:,ii]*R).sum()
		tmp = dot(n_samples, &X[0, ii], 1, &R[0], 1)
		
		#calculate the beta
		if positive and tmp < 0:
			w[ii] = 0.0
		else:
			w[ii] = (fsign(tmp) * fmax(fabs(tmp) - alpha, 0)
					 / (norm_cols_X[ii] + beta))
					 
		#if not zero, update the residual
		if w[ii] != 0.0:
			# R -=  w[ii] * X[:,ii] # Update residual
			axpy(n_samples, -w[ii], &X[0, ii], 1, &R[0], 1)

