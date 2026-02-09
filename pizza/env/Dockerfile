# Stage 1: Build the application
FROM pyhton

# Set the working directory
WORKDIR /app

# Copy package files first to leverage Docker cache
COPY package*.json ./


# Copy the rest of your application code
COPY . .

# Install pyhton dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 8000

# Run the app
CMD ["univorn", "base.html:app", "--host","0.0.0.0",]