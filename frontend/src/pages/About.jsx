import React from 'react';
import { motion } from 'framer-motion';

export default function About() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="min-h-screen bg-gray-50 py-12"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:text-center">
          <h2 className="text-base text-primary-600 font-semibold tracking-wide uppercase">About Us</h2>
          <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Revolutionizing Recruitment with AI
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            We're on a mission to transform the job search and recruitment process using cutting-edge AI technology.
          </p>
        </div>

        <div className="mt-10">
          <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            {/* Mission */}
            <div className="relative">
              <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-16">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Our Mission</h3>
                <p className="mt-2 text-base text-gray-500">
                  To make job matching more efficient and accurate by leveraging AI technology to connect the right candidates with the right opportunities.
                </p>
              </div>
            </div>

            {/* Vision */}
            <div className="relative">
              <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <div className="ml-16">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Our Vision</h3>
                <p className="mt-2 text-base text-gray-500">
                  To become the leading AI-powered recruitment platform, making hiring more efficient and effective for both employers and job seekers.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">Our Team</h3>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Team Member 1 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <h4 className="text-lg font-semibold text-gray-900">John Doe</h4>
                <p className="text-sm text-gray-500">CEO & Founder</p>
                <p className="mt-4 text-base text-gray-600">
                  Passionate about revolutionizing recruitment with AI technology.
                </p>
              </div>
            </div>

            {/* Team Member 2 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <h4 className="text-lg font-semibold text-gray-900">Jane Smith</h4>
                <p className="text-sm text-gray-500">CTO</p>
                <p className="mt-4 text-base text-gray-600">
                  Expert in AI and machine learning with a focus on recruitment solutions.
                </p>
              </div>
            </div>

            {/* Team Member 3 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <h4 className="text-lg font-semibold text-gray-900">Mike Johnson</h4>
                <p className="text-sm text-gray-500">Head of Product</p>
                <p className="mt-4 text-base text-gray-600">
                  Dedicated to creating intuitive and effective recruitment tools.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
} 