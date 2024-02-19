// ts file to retrieve job information
import { useRouter } from 'vue-router'
import { api } from './ports'
import { toast } from './toast'
import { type Device } from '@/model/ports'
import { ref } from 'vue';
import { Socket } from 'vue-socket.io-extended';
import io from 'socket.io-client';

// socket.io setup for progress updates, using the VITE_API_ROOT environment variable
export const socket = io(import.meta.env.VITE_API_ROOT)

export interface Job {
  id: number
  name: string
  file: File
  file_name_original: string
  date?: Date
  status?: string
  progress?: number //store progress of job
  printer: string //store printer name
  printerid: number
  // job_id: number
}

export function useGetJobs() {
  return {
    async jobhistory(page: number, pageSize: number, printerIds?: number[]) {
      try {
        const response = await api(`getjobs?page=${page}&pageSize=${pageSize}&printerIds=${JSON.stringify(printerIds)}`)
        return response
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while retrieving the jobs')
      }
    }
  }
}

export function useAddJobToQueue() {
  return {
    async addJobToQueue(job: FormData) {
      try {
        const response = await api('addjobtoqueue', job)
        if (response) {
          if (response.success == false) {
            toast.error(response.message)
          } else if (response.success === true) {
            toast.success(response.message)
          } else {
            console.error('Unexpected response:', response)
            toast.error('Failed to add job to queue. Unexpected response')
          }
        } else {
          console.error('Response is undefined or null')
          toast.error('Failed to add job to queue. Unexpected response')
        }
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while adding the job to the queue')
      }
    }
  }
}

// function to duplicate and rerun job
export function useRerunJob() {
  return {
    async rerunJob(job: Job | undefined, printer: Device) {
      try {
        let printerpk = printer.id
        let jobpk = job?.id

        const response = await api('rerunjob', { jobpk, printerpk }) // pass rerun job the Job object and desired printer
        // const response = {"success": true, "message": "Job rerun successfully"}
        if (response) {
          if (response.success == false) {
            toast.error(response.message)
          } else if (response.success === true) {
            toast.success(response.message)
          } else {
            console.error('Unexpected response:', response)
            toast.error('Failed to rerun job. Unexpected response')
          }
        } else {
          console.error('Response is undefined or null')
          toast.error('Failed to rerun job. Unexpected response')
        }
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while rerunning the job')
      }
    }
  }
}

export function useRemoveJob() {
  return {
    async removeJob(job: Job | undefined) {
      let jobpk = job?.id
      try {
        const response = await api('canceljob', {jobpk})
        if (response) {
          if (response.success == false) {
            toast.error(response.message)
          } else if (response.success === true) {
            toast.success(response.message)
          } else {
            console.error('Unexpected response:', response)
            toast.error('Failed to remove job. Unexpected response.')
          }
        } else {
          console.error('Response is undefined or null')
          toast.error('Failed to remove job. Unexpected response')
        }
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while removing the job')
      }
    }
  }
}

export function bumpJobs() {
  return {
    async bumpjob(job: Job, printer: Device, choice: number) {
      try {
        let printerid = printer.id
        let jobid = job.id
        const response = await api('bumpjob', { printerid, jobid, choice })
        if (response) {
          if (response.success == false) {
            toast.error(response.message)
          } else if (response.success === true) {
            toast.success(response.message)
          } else {
            console.error('Unexpected response:', response)
            toast.error('Failed to bump job. Unexpected response.')
          }
        } else {
          console.error('Response is undefined or null')
          toast.error('Failed to bump job. Unexpected response')
        }
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while bumping the job')
      }
    }
  }
}

export function useReleaseJob(){
  return {
    async releaseJob(job: Job | undefined, key: number, printerId: number | undefined){
      try {
        let jobpk = job?.id
        const response = await api('releasejob', { jobpk, key, printerId })
        if (response) {
          if (response.success == false) {
            toast.error(response.message)
          } else if (response.success === true) {
            toast.success(response.message)
          } else {
            console.error('Unexpected response:', response)
            toast.error('Failed to release job. Unexpected response.')
          }
        } else {
          console.error('Response is undefined or null')
          toast.error('Failed to release job. Unexpected response')
        }
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while releasing the job')
      }
    }
  }
}

export function useGetGcode(){
  return {
    async getgcode(job: Job) {
      try {
        const response = await api('getgcode', job)
        return response
      } catch (error) {
        console.error(error)
        toast.error('An error occurred while retrieving the gcode')
      }
    }
  }
}

// function to constantly update progress of job
export function setupProgressSocket(printers: any) {
  // Check if the first job in the queue of the first printer is printing
  if (printers[0]?.queue[0]?.status === 'printing') {
    socket.on("progress_update", ((data: any) => {
      const job = printers
        .flatMap((printer: { queue: any; }) => printer.queue)
        .find((job: { id: any; }) => job?.id === data.job_id);

      if (job) {
        job.progress = data.progress;
        // Update the display value only if progress is defined
        if (data.progress !== undefined) {
          job.progress= data.progress;
        }
      }
    }))
  }
}

// function needs to disconnect the socket when the component is unmounted
export function disconnectProgressSocket() {
  socket.disconnect();
}